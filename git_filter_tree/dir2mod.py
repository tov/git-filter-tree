"""
History rewrite helper script: Convert subfolder to submodule.

Usage:
    git-filter-tree dir2mod TREEMAP FOLDER URL [NAME] [-- REFS]

Arguments:

    TREEMAP     Path to tree index. For every top-level tree there should be
                a line "$TREE_SHA1 $COMMIT_SHA1" that contains the SHA1 of the
                target commit.
    FOLDER      Subfolder to replace.
    URL         URL of the submodule
    NAME        Name of the submodule (defaults to FOLDER)
    REFS        `git-rev-list` options

See also: http://coldfix.de/2017/06/13/git-dir2mod
"""

from .tree_filter import TreeFilter, cached

import os


class Dir2Mod(TreeFilter):

    # TODO: treemap -> commitmap
    def __init__(self, treemap, folder, url, name=None):
        super().__init__()
        self.path = folder
        self.url = url
        self.name = name or folder
        with open(treemap) as f:
            items = [line.strip().split() for line in f]
        self.commit_for_tree = dict(items)
        if len(self.commit_for_tree) != len(items):
            raise ValueError(
                "Error: several commits corresponding to the same subdir tree!\n"
                "This script can currently not deal with reverts within the subdirectory.\n"
                "You would end up with an incorrect history.")

    def depends(self, obj):
        return (obj.sha1, obj.path, obj.mode)

    @cached
    async def rewrite_file(self, obj):
        mode, kind, sha1, name = obj
        if name == '.gitattributes':
            text = obj.sha1 and await self.read_blob(obj.sha1) or b""
            sha1 = await self.write_blob("\n".join(
                line for line in text.decode('utf-8').splitlines()
                if not line.startswith(self.path + '/')
            ).encode('utf-8'))
        return [(mode, kind, sha1, name)]

    @cached
    async def rewrite_tree(self, obj):
        if obj.path == self.path:
            commit = self.commit_for_tree[obj.sha1]
            return [(0o160000, 'commit', commit, obj.name, True)]
        # only recurse into `self.path`:
        elif not obj.path or self.path.startswith(obj.path + '/'):

            old_entries = await self.read_tree(obj.sha1)
            new_entries = await self.map_tree(obj, old_entries)
            has_folder = max(map(len, new_entries)) == 5

            if not has_folder:
                return [obj[:]]

            if not obj.path:
                i = next((i for i, e in enumerate(new_entries)
                          if e[3] == '.gitmodules'), None)
                if i is None:
                    new_entries.append(await self.gitmodules_file(None))
                else:
                    new_entries[i] = await self.gitmodules_file(new_entries[i][2])

            sha1 = await self.write_tree(new_entries)
            return [(obj.mode, obj.kind, sha1, obj.name, True)]

        else:
            return [obj[:]]

    @cached
    async def gitmodules_file(self, sha1):
        text = sha1 and await self.read_blob(sha1) or b""
        sha1 = await self.write_blob((text.decode('utf-8') + """
[submodule "{}"]
    path = {}
    url = {}
"""[1:].format(self.name, self.path, self.url)).encode('utf-8'))
        return (0o100644, 'blob', sha1, '.gitmodules')


main = Dir2Mod.main
if __name__ == '__main__':
    import sys; sys.exit(main())

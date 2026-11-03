# A6 LOCAL-005 final save-file symlink guard — 2026-11-03

**Scope:** only the standalone LocalSavePaths platform helper; not the game's original .rgd serializer.

## Reproduction and repair
A Linux temporary-file experiment constructed ordinary profile/world directories and a world.sav symbolic link to an outside file. Writing through that leaf replaced the external file. Existing A6 protections checked directories, not the final save file.
Source commit: https://github.com/alwansan/raf/commit/66d8e67da5b4ee610526452ccfb763b6c10e52fc
Two helper methods now check the save-file leaf using File.GetAttributes / FileAttributes.ReparsePoint and refuse redirected targets. Three .NET8 C# Smoke tests cover real external file, dangling link and ordinary existing file.

## Execution evidence
- First source CI https://github.com/alwansan/raf/actions/runs/41623327576 FAILED: 14/15 Smoke. The test assumed File.Exists(danglingLink) was false on .NET8 Linux; runner observed true for link entry.
- Test-only correction https://github.com/alwansan/raf/commit/d01f4c4bfab342dc2eba35c569151cac9b292973 asserted actual ReparsePoint metadata and separately checked absent target.
- Final same-source https://github.com/alwansan/raf/actions/runs/41623564391 SUCCESS on d01f4c4: 24 successful steps, netstandard2.1 build with zero errors, Smoke 15/15. Job ID 125875127086.

## Limits
No Unity or Android phone execution; no demonstrated original SaveAndLoad use of world.sav; no .rgd serialize/deserialize test. Managed prechecks cannot guarantee atomic safety against hostile concurrent link replacement. No .meta, GUID, original assets, LFS, game source or native request changed. LOCAL-005 OPEN, overall NOT_READY and 0/3 complete candidate reviews.

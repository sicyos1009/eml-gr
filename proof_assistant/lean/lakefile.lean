import Lake
open Lake DSL

package «emlgr-seed» where
  -- Minimal package for CI seed checks.

lean_lib EMLGRSeedExecutable where
  srcDir := "."

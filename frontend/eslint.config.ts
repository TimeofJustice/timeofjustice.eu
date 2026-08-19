import js from "@eslint/js";
import globals from "globals";
import tseslint from "typescript-eslint";
import pluginVue from "eslint-plugin-vue";
import configPrettier from "eslint-config-prettier/flat";
import { defineConfig } from "eslint/config";

export default defineConfig([
  {
    ignores: ["dist/**", "harness-dist/**", "src/components.d.ts"],
  },
  {
    files: ["**/*.{js,mjs,cjs,ts,mts,cts,vue}"],
    plugins: { js },
    extends: ["js/recommended"],
    languageOptions: { globals: globals.browser },
  },
  tseslint.configs.recommended,
  pluginVue.configs["flat/recommended"],
  {
    files: ["**/*.vue"],
    languageOptions: { parserOptions: { parser: tseslint.parser } },
  },

  // Must come after all presets: turns off every rule that overlaps with
  // Prettier (indentation, line breaks, quotes, ...).
  configPrettier,

  {
    rules: {
      // --- Deliberately disabled from the presets ---

      // Pure cosmetics. Would reorder ~260 attributes in the existing code
      // and does not catch a single bug.
      "vue/attributes-order": "off",
      // Props are declared through TypeScript types here; optional props
      // do not need a runtime default.
      "vue/require-default-prop": "off",

      // --- Relaxed so they do not block while developing ---

      // Visible, but not a hard error.
      "@typescript-eslint/no-explicit-any": "warn",
      // Mark unused things on purpose: anything prefixed with _ is fine.
      "@typescript-eslint/no-unused-vars": [
        "error",
        {
          argsIgnorePattern: "^_",
          varsIgnorePattern: "^_",
          caughtErrorsIgnorePattern: "^_",
          destructuredArrayIgnorePattern: "^_",
        },
      ],

      // --- Additions that catch real bugs ---

      // Forgotten debug logging; console.warn/error stay allowed.
      "no-console": ["warn", { allow: ["warn", "error"] }],
      // Type coercion via == is a classic source of bugs.
      eqeqeq: ["error", "smart"],
      // let that is never reassigned (auto-fixable).
      "prefer-const": "error",
      "no-var": "error",
      // A loop that break/return always cuts short after one iteration.
      "no-unreachable-loop": "error",
      // Race condition: assigning to a variable that may be stale across an await.
      "require-atomic-updates": "error",
    },
  },
]);

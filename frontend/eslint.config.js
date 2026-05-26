// @ts-check
import react from 'eslint-plugin-react';
import jsxA11y from 'eslint-plugin-jsx-a11y';
import jsdoc from 'eslint-plugin-jsdoc';
import tseslint from 'typescript-eslint';
import reactHooks from 'eslint-plugin-react-hooks';
import pluginRouter from '@tanstack/eslint-plugin-router';
import { fixupPluginRules } from '@eslint/compat';
import ts from 'typescript';

const reactPlugin = fixupPluginRules(react);
const reactHooksPlugin = fixupPluginRules(reactHooks);
const jsxA11yPlugin = fixupPluginRules(jsxA11y);

export default [
  {
    ignores: ['dist', 'coverage', 'node_modules', '*.config.{js,ts}'],
  },
  ...tseslint.configs.recommended,
  ...pluginRouter.configs['flat/recommended'],
  {
    files: ['**/*.{ts,tsx,js,jsx}'],
    languageOptions: {
      ecmaVersion: 'latest',
      sourceType: 'module',
      parser: tseslint.parser,
      parserOptions: {
        ecmaFeatures: {
          jsx: true,
        },
      },
    },
    plugins: {
      '@typescript-eslint': tseslint.plugin,
      jsdoc,
      react: reactPlugin,
      'react-hooks': reactHooksPlugin,
      '@tanstack/router': pluginRouter,
      'jsx-a11y': jsxA11yPlugin,
    },
    settings: {
      react: { version: 'detect' },
    },
    rules: {
      // Recommended
      // ...tseslint.configs.recommended,
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,
      // ...pluginRouter.configs['flat/recommended'],
      ...jsxA11y.configs.recommended.rules,
      ...jsdoc.configs['flat/recommended-typescript'].rules,

      // JSDoc
      'jsdoc/require-jsdoc': [
        'warn',
        {
          require: {
            FunctionDeclaration: true,
            MethodDefinition: true,
            ClassDeclaration: true,
            ArrowFunctionExpression: false,
            FunctionExpression: false,
          },
        },
      ],
      'jsdoc/require-param': 'error',
      'jsdoc/require-returns': 'error',
      'jsdoc/require-param-description': 'warn',
      'jsdoc/require-returns-description': 'warn',
      'jsdoc/require-returns-check': 'warn',
      'jsdoc/require-param-type': 'error',
      'jsdoc/require-returns-type': 'error',
      'jsdoc/require-property-type': 'error',
      'jsdoc/no-types': 'off',

      // TypeScript
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/explicit-function-return-type': 'warn',
      '@typescript-eslint/consistent-type-definitions': ['error', 'interface'],
      '@typescript-eslint/no-unused-vars': [
        'warn',
        { argsIgnorePattern: '^_', varsIgnorePattern: '^_' },
      ],
      
      // React
      'react/react-in-jsx-scope': 'off',
      'react/jsx-uses-react': 'off',

      // Custom and Overrides
      quotes: ['error', 'single', { avoidEscape: true }],
      semi: ['error', 'always'],
    },
  },
  {
    files: ['**/tests/**/*.{ts,tsx}'],
    rules: {
      // Recommended
      ...react.configs.recommended.rules,
      ...reactHooks.configs.recommended.rules,

      // TypeScript
      '@typescript-eslint/no-explicit-any': 'warn',
      '@typescript-eslint/no-unused-vars': 'off',

      // React
      'react/react-in-jsx-scope': 'off',
      'react/jsx-uses-react': 'off',

      // Custom and Overrides
      semi: ['error', 'always'],
    },
  },
  {
    files: ['src/lib/ws.ts', 'tests/e2e/**/*.ts'],
    rules: {
      'jsdoc/require-param': 'off',
      'jsdoc/require-param-type': 'off',
      'jsdoc/require-param-description': 'off',
      'jsdoc/require-returns': 'off',
      'jsdoc/require-returns-type': 'off',
      'jsdoc/require-returns-description': 'off',
    },
  },
];

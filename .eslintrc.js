module.exports = {
    parserOptions: {
        ecmaVersion: 'latest',
        jsx: true,
    },
    extends: [
        'eslint:recommended',
        'next/core-web-vitals',
        'plugin:@typescript-eslint/recommended',
        'plugin:prettier/recommended',
    ],
    rules: {
        indent: ['error', 4],
        'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
        'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    },
};

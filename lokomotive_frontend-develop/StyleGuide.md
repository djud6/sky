# SkyIT React/JSX Style Guide

## Table of Contents

1. [IDE Setup](#ide-setup)
1. [Basic Rules](#basic-rules)
1. [Functional Components vs Class-Based Components](#functional-components-vs-class-based-components)
1. [Mixins](#mixins)
1. [Naming](#naming)
1. [Alignment](#alignment)
1. [Quotes](#quotes)
1. [Spacing](#spacing)
1. [Props](#props)
1. [Parentheses](#parentheses)
1. [Tags](#tags)
1. [Methods](#methods)
1. [Imports](#imports)
1. [PropTypes](#proptypes)
1. [Prettier](#prettier)

## IDE Setup
- Before you started, please make sure you have set up the setting of your IDE(Visual Studio Code in our case) to auto-format and validate the lint on Save
- Make sure you have run `npm install` before the setup
- Make sure you have installed the `ESLint` extension if not, please install the `ESLint` extension before continue.
- Make sure you have installed the `Prettier - Code formatter` extension if not, please install the `Prettier - Code formatter` extension before continue.

#### Here are the steps:

1. Open `Preferences -> Settings` page
2. Type and search `code actions on save`
3. Click on the link `Edit in settings.json`
4. Within the `settings.json`, add the following code to the file:
```
  "editor.defaultFormatter": "esbenp.prettier-vscode",
  // Enable per-language
  "[javascript]": {
      "editor.formatOnSave": true
  },
  // Enable per-language
  "[javascriptreact]": {
      "editor.formatOnSave": true
  },
  "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
  },
  "eslint.validate": ["javascript"]
```
5. Save the file and you are all set!

After the setup, the IDE will auto-format your current opened file when you hit on `save` or `ctr + c`, also the ESLint will validate the current opened file and list all the issues in the `PROBLEMS` tab. Make sure to address all of them before creating any pull request in the future.


## Basic Rules

- Each file should contain one React component which is to be used outside that file. Additional components may be included in the same file provided they are only used as children of the main component; if required by another component, they should be moved into their own file.
- Always use JSX syntax
- Do not use React.createElement unless unavoidable
- Statements should end with semi-colons even when not strictly required, to avoid unexpected behaviour if the interpreter infers semi-colons in the wrong location

## Functional Components vs. Class-Based Components

- Subject to the guidance of the React project, and in recognition that this is a new code-base, function-based components and Hooks are to be preferred over class-based components, even where state is involved.

- Arrow function are preferred as a convention over other forms of function declaration.

## Mixins

- Mixins are to be avoided, as they introduce sources of complexity and the potential for bugs

## Naming

- **Extensions**: Use '.js' for React components, '.css' for pure CSS files.
- **File Names**: Use PascalCase for filenames, name files after the primary component they contain or 'index.js' for a top-level file in a subfolder.
- **Reference Naming**: Use PascalCase for components and camelCase for instances.

  ```jsx
  // bad
  import reservationCard from "./ReservationCard";

  // good
  import ReservationCard from "./ReservationCard";

  // bad
  const ReservationItem = <ReservationCard />;

  // good
  const reservationItem = <ReservationCard />;
  ```

- **Props Naming**: `style` and `className` should be used exclusively for values which are passsed to rendered components to avoid any unexpected behaviour. Props should be explictly named in all cases:

  ```
  // bad
  const Component = (props) => {
    return (<div>{props.foo}</div>);
  };

  // good
  const Component = ({foo}) => {
    return (<div>{foo}</div>);
  };
  ```

## Alignment

- Follow these alignment styles for JSX syntax. eslint: [`react/jsx-closing-bracket-location`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-closing-bracket-location.md) [`react/jsx-closing-tag-location`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-closing-tag-location.md)

  ```jsx
  // bad
  <Foo superLongParam="bar"
       anotherSuperLongParam="baz" />

  // good
  <Foo
    superLongParam="bar"
    anotherSuperLongParam="baz"
  />

  // if props fit in one line then keep it on the same line
  <Foo bar="bar" />

  // children get indented normally
  <Foo
    superLongParam="bar"
    anotherSuperLongParam="baz"
  >
    <Quux />
  </Foo>

  // bad
  {showButton &&
    <Button />
  }

  // bad
  {
    showButton &&
      <Button />
  }

  // good
  {showButton && (
    <Button />
  )}

  // good
  {showButton && <Button />}

  // good
  {someReallyLongConditional
    && anotherLongConditional
    && (
      <Foo
        superLongParam="bar"
        anotherSuperLongParam="baz"
      />
    )
  }

  // good
  {someConditional ? (
    <Foo />
  ) : (
    <Foo
      superLongParam="bar"
      anotherSuperLongParam="baz"
    />
  )}
  ```

## Quotes

- Always use double quotes (`"`) for JSX attributes, but single quotes (`'`) for all other JS. eslint: [`jsx-quotes`](https://eslint.org/docs/rules/jsx-quotes)

  > Why? Regular HTML attributes also typically use double quotes instead of single, so JSX attributes mirror this convention.

  ```jsx
  // bad
  <Foo bar='bar' />

  // good
  <Foo bar="bar" />

  // bad
  <Foo style={{ left: "20px" }} />

  // good
  <Foo style={{ left: '20px' }} />
  ```

## Spacing

- Always include a single space in your self-closing tag. eslint: [`no-multi-spaces`](https://eslint.org/docs/rules/no-multi-spaces), [`react/jsx-tag-spacing`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-tag-spacing.md)

  ```jsx
  // bad
  <Foo/>

  // very bad
  <Foo                 />

  // bad
  <Foo
   />

  // good
  <Foo />
  ```

- Do not pad JSX curly braces with spaces. eslint: [`react/jsx-curly-spacing`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-curly-spacing.md)

  ```jsx
  // bad
  <Foo bar={ baz } />

  // good
  <Foo bar={baz} />
  ```

## Props

- Always use camelCase for prop names, or PascalCase if the prop value is a React component.

  ```jsx
  // bad
  <Foo
    UserName="hello"
    phone_number={12345678}
  />

  // good
  <Foo
    userName="hello"
    phoneNumber={12345678}
    Component={SomeComponent}
  />
  ```

- Omit the value of the prop when it is explicitly `true`. eslint: [`react/jsx-boolean-value`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-boolean-value.md)

  ```jsx
  // bad
  <Foo
    hidden={true}
  />

  // good
  <Foo
    hidden
  />

  // good
  <Foo hidden />
  ```

- Always include an `alt` prop on `<img>` tags. If the image is presentational, `alt` can be an empty string or the `<img>` must have `role="presentation"`. eslint: [`jsx-a11y/alt-text`](https://github.com/evcohen/eslint-plugin-jsx-a11y/blob/master/docs/rules/alt-text.md)

  ```jsx
  // bad
  <img src="hello.jpg" />

  // good
  <img src="hello.jpg" alt="Me waving hello" />

  // good
  <img src="hello.jpg" alt="" />

  // good
  <img src="hello.jpg" role="presentation" />
  ```

- Do not use words like "image", "photo", or "picture" in `<img>` `alt` props. eslint: [`jsx-a11y/img-redundant-alt`](https://github.com/evcohen/eslint-plugin-jsx-a11y/blob/master/docs/rules/img-redundant-alt.md)

  > Why? Screenreaders already announce `img` elements as images, so there is no need to include this information in the alt text.

  ```jsx
  // bad
  <img src="hello.jpg" alt="Picture of me waving hello" />

  // good
  <img src="hello.jpg" alt="Me waving hello" />
  ```

- Use only valid, non-abstract [ARIA roles](https://www.w3.org/TR/wai-aria/#usage_intro). eslint: [`jsx-a11y/aria-role`](https://github.com/evcohen/eslint-plugin-jsx-a11y/blob/master/docs/rules/aria-role.md)

  ```jsx
  // bad - not an ARIA role
  <div role="datepicker" />

  // bad - abstract ARIA role
  <div role="range" />

  // good
  <div role="button" />
  ```

- Do not use `accessKey` on elements. eslint: [`jsx-a11y/no-access-key`](https://github.com/evcohen/eslint-plugin-jsx-a11y/blob/master/docs/rules/no-access-key.md)

> Why? Inconsistencies between keyboard shortcuts and keyboard commands used by people using screenreaders and keyboards complicate accessibility.

```jsx
// bad
<div accessKey="h" />

// good
<div />
```

- Avoid using an array index as `key` prop, prefer a stable ID. eslint: [`react/no-array-index-key`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/no-array-index-key.md)

> Why? Not using a stable ID [is an anti-pattern](https://medium.com/@robinpokorny/index-as-a-key-is-an-anti-pattern-e0349aece318) because it can negatively impact performance and cause issues with component state.

We don’t recommend using indexes for keys if the order of items may change.

```jsx
// bad
{
  todos.map((todo, index) => <Todo {...todo} key={index} />);
}

// good
{
  todos.map((todo) => <Todo {...todo} key={todo.id} />);
}
```

- Always define explicit defaultProps for all non-required props.

> Why? propTypes are a form of documentation, and providing defaultProps means the reader of your code doesn’t have to assume as much. In addition, it can mean that your code can omit certain type checks.

```jsx
// bad
function SFC({foo, bar, children}) {
  return (
    <div>
      {foo}
      {bar}
      {children}
    </div>
  );
}
SFC.propTypes = {
  foo: PropTypes.number.isRequired,
  bar: PropTypes.string,
  children: PropTypes.node,
};

// good
function SFC({foo, bar, children}) {
  return (
    <div>
      {foo}
      {bar}
      {children}
    </div>
  );
}
SFC.propTypes = {
  foo: PropTypes.number.isRequired,
  bar: PropTypes.string,
  children: PropTypes.node,
};
SFC.defaultProps = {
  bar: "",
  children: null,
};
```

## Parentheses

- Wrap JSX tags in parentheses at all times, whether multiline or single line.

> Why? This helps improve readability and minimizes the chance of code standards being violated in the event that a single line of JSX is split in the future.

## Tags

- Always self-close tags that have no children. eslint: [`react/self-closing-comp`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/self-closing-comp.md)

  ```jsx
  // bad
  <Foo variant="stuff"></Foo>

  // good
  <Foo variant="stuff" />
  ```

- If your component has multiline properties, close its tag on a new line. eslint: [`react/jsx-closing-bracket-location`](https://github.com/yannickcr/eslint-plugin-react/blob/master/docs/rules/jsx-closing-bracket-location.md)

  ```jsx
  // bad
  <Foo
    bar="bar"
    baz="baz" />

  // good
  <Foo
    bar="bar"
    baz="baz"
  />
  ```

## Methods

- Prefer arrow functions over other sorts of functions unless this-binding is explicitly required

## Imports

- Imports should be ordered as follows: packages, reused components, component-specific files.

  ```jsx
  import React from 'react';

  import PanelHeader from '../helpers/PanelHeader';
  ...

  import 'Example.css';
  ```

## PropTypes

- PropTypes should be used for all new code going forward and re-factored into existing code as appropriate.

## Prettier - Code Formatter

- Use [Prettier - Code Formatter plugin for VSCode](https://marketplace.visualstudio.com/items?itemName=esbenp.prettier-vscode#configuration) for consistent formatting.
- All settings are in `.prettierrc` file in the root folder of the project. For options use [official config guide](https://prettier.io/docs/en/options.html).

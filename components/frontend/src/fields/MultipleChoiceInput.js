import React, { Component } from 'react';
import { Form } from 'semantic-ui-react';

class MultipleChoiceInput extends Component {
  constructor(props) {
    super(props);
    this.state = { value: props.value, options: this.options() }
  }
  componentDidUpdate(prevProps) {
    if (prevProps.values !== this.props.values) {
      this.setState({ options: this.options() })
    }
    if (prevProps.value !== this.props.value) {
      this.setState({ value: this.props.value })
    }
  }
  options() {
    let options = [];
    this.props.options.forEach((option) => {options.push({key: option, text: option, value: option})});
    this.props.value.forEach((val) => {options.push({key: val, text: val, value: val})});
    options.sort((a, b) => a.text.localeCompare(b.text));
    return options;
  }
  handleAddition = (event, { value }) => {
    event.preventDefault();
    this.setState({
      options: [{ key: value, text: value, value: value }, ...this.state.options],
    })
  }
  onSubmit(event, value) {
    event.preventDefault();
    if (value !== this.props.value) {
      this.props.set_value(value);
    }
  }
  render() {
    let { set_value, allowAdditions, ...otherProps } = this.props;
    return (
      <Form>
        {this.props.readOnly ?
          <Form.Input
            {...otherProps}
          />
          :
          <Form.Dropdown
            {...otherProps}
            allowAdditions={allowAdditions}
            fluid
            multiple
            onAddItem={this.handleAddition}
            onChange={(e, { value }) => this.onSubmit(e, value)}
            options={this.state.options}
            search
            selection
            value={this.state.value || []}
          />
        }
      </Form>
    )
  }
}

export { MultipleChoiceInput };

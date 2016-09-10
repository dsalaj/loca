var Comment = React.createClass({
  render: function () {
    return (
      <div className="comment">
        <span className="commentAuthor">
          <b>{this.props.author}: </b>
        </span>
        {this.props.children}
      </div>
    );
  }
});

var CommentList = React.createClass({
  render: function() {
    var commentNodes = this.props.data.reverse().map(function (comment) {
      return (
        <Comment author={comment.author} key={comment.id}>
          {comment.text}
        </Comment>
      );
    });
    return (
      <div className="commentList">
        {commentNodes}
      </div>
    );
  }
});

var RegisterForm = React.createClass({
  getInitialState: function() {
    return {nickname: ''};
  },
  handleNickChange: function(e) {
    this.setState({nickname: e.target.value});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    var nickname = this.state.nickname.trim();
    if (!nickname) {
      return;
    }
    this.props.onNicknameSubmit({nickname: nickname});
    this.setState({nickname: ''});
    // TODO: hide the registration form
  },
  render: function () {
    return (
      <div className="registerForm">
        <form className="registerForm" onSubmit={this.handleSubmit}>
          <input type="text"
                 placeholder="Choose a nickname"
                 value={this.state.nickname}
                 onChange={this.handleNickChange}
          />
          <input type="submit" value="Login" />
        </form>
      </div>
    );
  }
});

var CommentForm = React.createClass({
  getInitialState: function() {
    return {text: ''};
  },
  handleAuthorChange: function(e) {
    this.setState({author: e.target.value});
  },
  handleTextChange: function(e) {
    this.setState({text: e.target.value});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    // var author = this.state.author.trim();
    var text = this.state.text.trim();
    if (!text) {
      return;
    }
    this.props.onCommentSubmit({text: text});
    this.setState({text: ''});
  },
  render: function() {
    return (
      <div className="commentForm">
        <form className="commentForm" onSubmit={this.handleSubmit}>
          {/*<input type="text"*/}
                 {/*placeholder="Your name"*/}
                 {/*value={this.state.author}*/}
                 {/*onChange={this.handleAuthorChange}*/}
          {/*/>*/}
          <input type="text"
                 placeholder="Say something..."
                 value={this.state.text}
                 onChange={this.handleTextChange}
          />
          <input type="submit" value="Post" />
        </form>
      </div>
    );
  }
});

var CommentBox = React.createClass({
  getInitialState: function () {
    return {data: [], socket: null};
  },
  componentDidMount: function() {
    this.state.socket = io.connect('http://' + document.domain + ':' + location.port + this.props.url);
    this.state.socket.on('connect', () => {
      // console.log('Socket connect event happened');
      // this.state.socket.emit('my_event', {data: {text: 'I\'m connected!', author: 'SERVER', id: '123123'}});
    });
    this.state.socket.on('my_response', (response) => {
      this.setState({data: response.data});
    });
  },
  handleCommentSubmit: function(comment) {
    this.state.socket.emit('my_msg', {data: comment});
  },
  handleRegisterSubmit: function (form_data) {
    this.state.socket.emit('register', {data: form_data.nickname})
  },
  render: function() {
    return (
      <div className="commentBox">
        <h1>Comments</h1>
        <CommentList data={this.state.data}/>
        <CommentForm onCommentSubmit={this.handleCommentSubmit}/>
        <RegisterForm onNicknameSubmit={this.handleRegisterSubmit}/>
      </div>
    );
  }
});

ReactDOM.render(
  <CommentBox url="/api/chat" />,
  document.getElementById('content')
);

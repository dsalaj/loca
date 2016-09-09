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
    var commentNodes = this.props.data.map(function (comment) {
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

var CommentForm = React.createClass({
  getInitialState: function() {
    return {author: '', text: ''};
  },
  handleAuthorChange: function(e) {
    this.setState({author: e.target.value});
  },
  handleTextChange: function(e) {
    this.setState({text: e.target.value});
  },
  handleSubmit: function(e) {
    e.preventDefault();
    var author = this.state.author.trim();
    var text = this.state.text.trim();
    if (!text || !author) {
      return;
    }
    this.props.onCommentSubmit({author: author, text: text});
    this.setState({author: '', text: ''});
  },
  render: function() {
    return (
      <div className="commentForm">
        <form className="commentForm" onSubmit={this.handleSubmit}>
          <input type="text"
                 placeholder="Your name"
                 value={this.state.author}
                 onChange={this.handleAuthorChange}
          />
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
  loadCommentsFromServer: function() {
    // $.ajax({
    //   url: this.props.url,
    //   dataType: 'json',
    //   cache: false,
    //   success: function(data) {
    //     this.setState({data: data});
    //   }.bind(this),
    //   error: function(xhr, status, err) {
    //     console.error(this.props.url, status, err.toString());
    //   }.bind(this)
    // });
  },
  getInitialState: function () {
    return {data: [], socket: null};
  },
  componentDidMount: function() {
    // this.loadCommentsFromServer();
    // setInterval(this.loadCommentsFromServer, this.props.pollInterval);

    this.state.socket = io.connect('http://' + document.domain + ':' + location.port + this.props.url);
    this.state.socket.on('connect', () => {
      console.log('Socket connect event happened');
      this.state.socket.emit('my_event', {data: {text: 'I\'m connected!', author: 'SERVER', id: '123123'}});
    });
    this.state.socket.on('my_response', (response) => {
      // console.log(response.data);
      this.state.data.push(response.data);
      // console.log(this.state.data);
      this.setState({data: this.state.data});
    });
  },
  handleCommentSubmit: function(comment) {
    // $.ajax({
    //   url: this.props.url,
    //   dataType: 'json',
    //   type: 'POST',
    //   data: comment,
    //   success: function(data) {
    //     this.setState({data: data});
    //   }.bind(this),
    //   error: function(xhr, status, err) {
    //     console.error(this.props.url, status, err.toString());
    //   }.bind(this)
    // });
    this.state.socket.emit('my_msg', {data: comment});
  },
  render: function() {
    console.log("CommentBox data", this.state.data);
    return (
      <div className="commentBox">
        <h1>Comments</h1>
        <CommentList data={this.state.data}/>
        <CommentForm onCommentSubmit={this.handleCommentSubmit}/>
      </div>
    );
  }
});

ReactDOM.render(
  <CommentBox url="/api/comments" pollInterval={1000} />,
  document.getElementById('content')
);

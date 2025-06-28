function init() {
    // ゲームの状態を初期化します。
    var board = new Board(5, 10);
    var currentBlock = new Block();
    var score = 0;
  
    // タイマーを設定します。
    window.setInterval(update, 200);
  }
  
  function update() {
    // ブロックを落とします。
    currentBlock.fall();
  
    // ブロックが下まで落ちたら、削除します。
    if (currentBlock.isAtBottom()) {
      board.removeBlock(currentBlock);
      score += board.clearLines();
      currentBlock = new Block();
    }
  
    // キー入力をチェックします。
    if (window.event.keyCode === 37) {
      currentBlock.moveLeft();
    } else if (window.event.keyCode === 38) {
      currentBlock.rotate();
    } else if (window.event.keyCode === 39) {
      currentBlock.moveRight();
    }
  
    // キャンバスに描画します。
    board.draw(canvas);
    currentBlock.draw(canvas);
  }
  
  window.onload = init;
  
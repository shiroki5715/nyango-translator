const messageEl = document.getElementById('message');
const pupilEl = document.getElementById('pupil');

const messages = [
    'たすけて...',
    'ここはどこ？',
    'だれか見てる？',
    'ノイズが聞こえる...',
    'あなたはだれ？',
    '壁の向こうに何かいる...',
    '出口はない。',
];

let messageIndex = 0;
let charIndex = 0;

function typeMessage() {
    if (charIndex < messages[messageIndex].length) {
        messageEl.textContent += messages[messageIndex].charAt(charIndex);
        charIndex++;
        setTimeout(typeMessage, 150); // 次の文字を表示するまでの時間
    } else {
        setTimeout(() => {
            messageEl.textContent = '';
            charIndex = 0;
            messageIndex = (messageIndex + 1) % messages.length;
            typeMessage();
        }, 3000); // 次のメッセージを表示するまでの待機時間
    }
}

document.addEventListener('mousemove', (e) => {
    const eyeContainer = document.getElementById('eye-container').getBoundingClientRect();
    const eyeX = eyeContainer.left + eyeContainer.width / 2;
    const eyeY = eyeContainer.top + eyeContainer.height / 2;

    const angle = Math.atan2(e.clientY - eyeY, e.clientX - eyeX);

    const pupilX = Math.cos(angle) * (eyeContainer.width / 4);
    const pupilY = Math.sin(angle) * (eyeContainer.height / 4);

    pupilEl.style.transform = `translate(${pupilX}px, ${pupilY}px)`;
});

typeMessage();

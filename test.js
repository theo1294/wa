const axios = require('axios');

const accessToken = 'EAAD6V7os0gcBOZBgupkhgNfv3IG5R5C8kzztMvf4ZCZAY3BDIYjvSgesfjLUlJWZCgc6EeMsmZAbOsnT3TRZBz8k1QlFUvPFsXYeTY3Kk9lcU3O5bLuSsqPtEQMUz2ggynZC1fk1lT9lMVkWPH4ojIdiYEn4s1mor9aJaccTLZB2nRyOPmYE1uICLnRXHeEnemAp6gZDZD'; // ACCESS TOKEN HERE
const shareUrl = 'https://www.facebook.com/100085898449586/posts/596121356594474/?mibextid=hnQQrChkSqkykvoJ'; // URL HERE
const shareCount = 100;
const timeInterval = 50;
const deleteAfter = 60 * 60;

let sharedCount = 0;
let timer = null;

async function sharePost() {
  try {
    const response = await axios.post(
      `https://graph.facebook.com/me/feed?access_token=${accessToken}&fields=id&limit=1&published=0`,
      {
        link: shareUrl,
        privacy: { value: 'SELF' },
        no_story: true,
      },
      {
        muteHttpExceptions: true,
        headers: {
          authority: 'graph.facebook.com',
          'cache-control': 'max-age=0',
          'sec-ch-ua-mobile': '?0',
          'user-agent':
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
          },
          method: 'post',
      }
    );

    sharedCount++;
    const postId = response?.data?.id;

    console.log(`Post shared: ${sharedCount}`);
    console.log(`Post ID: ${postId || 'Unknown'}`);

    if (sharedCount === shareCount) {
      clearInterval(timer);
      console.log('Finished sharing posts.');

      if (postId) {
        setTimeout(() => {
          deletePost(postId);
        }, deleteAfter * 1000);
      }
    }
  } catch (error) {
    console.error('Failed to share post:', error.response.data);
  }
}

async function deletePost(postId) {
  try {
    await axios.delete(`https://graph.facebook.com/${postId}?access_token=${accessToken}`);
    console.log(`Post deleted: ${postId}`);
  } catch (error) {
    console.error('Failed to delete post:', error.response.data);
  }
}

timer = setInterval(sharePost, timeInterval);

setTimeout(() => {
  clearInterval(timer);
  console.log('Loop stopped.');
}, shareCount * timeInterval);

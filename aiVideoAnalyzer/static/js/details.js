
document.getElementById('share-blog').addEventListener('click',function(event){
    const blogContent = document.getElementById('blogContent');
    const blog = blogContent.innerHTML;
    const youtubeLink = document.getElementById('saved-link').innerHTML;
    const prompt = 'If that sounds like a fit to you, click the following link to watch the full video: '
    sharedData = blog + prompt + youtubeLink;

    //common error that happens when we try to share the blog
    sharedData = sharedData.replace('                        ','');
    while (sharedData.includes('  ')){
        sharedData = sharedData.replace('  ',' ');

    }
    

    
    event.preventDefault();
    window.open('https://twitter.com/intent/post?text='+sharedData);
});
let currentIndex = 0;


async function nextContent() {
    // Increment the index for the next set of content
    currentIndex++;
    // Build the file paths for the next set of content
    const imagePath = `./output/image_${currentIndex}.png`;
    const storyPath = `./output/story_${currentIndex}.txt`;
    const titlePath = `./output/title_${currentIndex}.txt`;

    // Update the image directly
    const storyResponse = await fetch(imagePath);
    document.getElementById('book-image').src = imagePath;

    try {
        // Fetch and update the story text
        const storyResponse = await fetch(storyPath);
        const storyText = await storyResponse.text();
        const formattedStory = storyText.replace(/\n/g, '<br>');
        document.getElementById('book-text').innerHTML = formattedStory;

        // Fetch and update the title text
        const titleResponse = await fetch(titlePath);
        const titleText = await titleResponse.text();
        const formattedTitle = titleText.replace(/\n/g, '<br>');
        document.getElementById('book-title').innerHTML = formattedTitle;
    } catch (error) {
        console.error('Error fetching new content:', error);
    }
}



async function previousContent() {
    // Increment the index for the next set of content
    currentIndex = Math.max(currentIndex - 1, 1);
    // Build the file paths for the next set of content
    const imagePath = `./output/image_${currentIndex}.png`;
    const storyPath = `./output/story_${currentIndex}.txt`;
    const titlePath = `./output/title_${currentIndex}.txt`;

    // Update the image directly
    const storyResponse = await fetch(imagePath);
    document.getElementById('book-image').src = imagePath;

    try {
        // Fetch and update the story text
        const storyResponse = await fetch(storyPath);
        const storyText = await storyResponse.text();
        const formattedStory = storyText.replace(/\n/g, '<br>');
        document.getElementById('book-text').innerHTML = formattedStory;

        // Fetch and update the title text
        const titleResponse = await fetch(titlePath);
        const titleText = await titleResponse.text();
        const formattedTitle = titleText.replace(/\n/g, '<br>');
        document.getElementById('book-title').innerHTML = formattedTitle;
    } catch (error) {
        console.error('Error fetching new content:', error);
    }
}


// Prevent the default anchor click behavior


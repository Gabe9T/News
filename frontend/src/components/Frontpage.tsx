import React, { useState, useEffect } from 'react';
import { firestore } from '../firebaseConfig';

interface Story {
  title: string;
  text: string;
  date: string;
  link: string;
}

const Frontpage: React.FC = () => {
  const [stories, setStories] = useState<Story[]>([]);

  useEffect(() => {
    const fetchStories = async () => {
      try {
        const currentDate = new Date().toLocaleDateString('en-US', {
          month: '2-digit',
          day: '2-digit',
          year: '2-digit'
        }).replace(/\//g, '-');

        const storiesCollection = firestore.collection('stories').doc(currentDate).collection('stories');
        const snapshot = await storiesCollection.get();
        
        const fetchedStories: Story[] = [];
        snapshot.forEach((doc) => {
          const storyData = doc.data();
          fetchedStories.push({
            title: storyData.title,
            text: storyData.text,
            date: storyData.date,
            link: storyData.link,
          });
        });
        setStories(fetchedStories);
      } catch (error) {
        console.error('Error fetching stories:', error);
      }
    };

    fetchStories();
  }, []);

  return (
    <div>
      <h1>Today's Stories</h1>
      {stories.length === 0 ? (
        <p>No stories available for today</p>
      ) : (
        <ul>
          {stories.map((story, index) => (
            <li key={index}>
              <h2>{story.title}</h2>
              <p>{story.text}</p>
              <a href={story.link}>Read more</a>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
};

export default Frontpage;
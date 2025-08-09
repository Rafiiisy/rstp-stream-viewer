Full Stack Engineer Coding Test
Project: RTSP Stream Viewer
Overview
Build a simple web application that allows users to add RTSP stream URLs and view the
live streams in a browser. The application should be hosted on GitHub Pages or similar
service.
Required Deliverables
● GitHub repository with complete source code
● Live demo hosted on GitHub Pages or similar platform
● README with setup instructions
Technical Requirements
1. Frontend
● Create a clean, responsive web interface with:
○ Input field to add RTSP stream URLs
○ Display area for the live stream(s)
○ Option to view multiple streams simultaneously in a grid layout
○ Basic stream controls (play/pause)
● Use React.js for the frontend implementation
2. Backend
● Create a Django backend that:
○ Accepts RTSP stream URLs
○ Processes video streams using FFmpeg
○ Streams video to frontend using Django Channels (WebSockets)
○ Handles connection errors gracefully
3. Deployment
● Host the frontend on GitHub Pages or similar service
● Deploy the backend on a platform of your choice (Heroku, Vercel, etc.)
● Provide clear instructions for running the application locally
Evaluation Criteria
● Functionality: Streams display properly and smoothly
● Code quality and organization
● Error handling
● UI/UX design
● Performance with multiple streams
Test RTSP Streams
For testing purposes, you can use these public RTSP streams:
●
Submission Instructions
1. Send us the GitHub repository URL
2. Provide the URL to the live demo
3. Include any credentials needed to access the application (if applicable)
4. Timeline 7 days from the receipt of this test
Good luck!
rtsp://admin:admin123@49.248.155.178:555/cam/realmonitor?channel=1&subtype=0
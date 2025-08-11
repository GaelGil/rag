// import { useState, useEffect } from "react";
// import "../css/Home.css";
// import PostCard from "../components/ListItems/PostCard";
// // import { getRecentPosts } from "../api/posts";
// // import { searcUsers } from "../api/users";
// import { useNavigate } from "react-router-dom";
// import type { Post } from "../types/Post";
// // home component
// const FeedPage: React.FC = () => {
//   // state vars
//   const [searchQuery, setSearchQuery] = useState("");
//   const [posts, setPosts] = useState<Post[]>([]);
//   const [error, setError] = useState("");
//   const [loading, setLoading] = useState(true);
//   const navigate = useNavigate();

//   // when anything changes on the componet it runs again, setting
//   // the array at the end makes it so that theres no change
//   useEffect(() => {
//     const loadRecentPosts = async () => {
//       try {
//         const recentPosts = await getRecentPosts();
//         setPosts(recentPosts);
//       } catch (err) {
//         console.log(err);
//         setError("failed to load movies");
//       } finally {
//         setLoading(false);
//       }
//     };
//     loadRecentPosts();
//   }, []);

//   // function to handle a search
//   const handleSearch = async (e: React.FormEvent<HTMLFormElement>) => {
//     e.preventDefault(); // prevent default beavhior of reloading
//     if (!searchQuery.trim()) return; // if not full empty space
//     if (loading) return; // if we are loading return
//     setLoading(true);
//     try {
//       // const searchResults = await searcUsers(searchQuery); // get results
//       navigate("/users/");
//       //   setMovies(searchResults); // update the movies state with results
//       setError(""); // update error state with empty string
//     } catch {
//       setError("failed to load error"); // update the error state with error
//     } finally {
//       setLoading(false); // update the loading state to false
//     }
//   };

//   return (
//     <div className="home">
//       <form onSubmit={handleSearch} className="search-form">
//         <input
//           type="text"
//           placeholder="Search for movies..."
//           className="search-input"
//           value={searchQuery}
//           onChange={(e) => setSearchQuery(e.target.value)}
//         />
//         <button type="submit" className="search-button">
//           Search
//         </button>
//       </form>

//       {error && <div className="error-message">{error}</div>}

//       {loading ? (
//         <div className="loading">Loading...</div>
//       ) : (
//         <div className="movies-grid">
//           {posts.map((post) => (
//             <PostCard post={post} key={post.id} />
//           ))}
//         </div>
//       )}
//     </div>
//   );
// };

// export default FeedPage;

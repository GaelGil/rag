import Card from "react-bootstrap/Card";
import { useState, useEffect } from "react";
import UserCard from "../ListItems/UserCard";
import type { User } from "../../types/User";
import { getUserFollowers } from "../../api/users";

const Followers = ({ userId }: { userId: string }) => {
  const [followers, setFollowers] = useState<User[]>([]);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchFriends = async () => {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token || !userId) {
        return;
      }
      try {
        const userFollowers = await getUserFollowers(userId, token);
        setFollowers(userFollowers);
      } catch (error) {
        console.error("Error fetching friends", error);
      } finally {
        setLoading(false);
      }
    };

    if (userId) {
      fetchFriends();
    }
  }, [userId]);

  return (
    <>
      <Card style={{ width: "18rem" }}>
        <Card.Body>
          {loading ? (
            <Card.Header as="h2">Loading</Card.Header>
          ) : followers.length === 0 ? (
            <Card.Header as="h2">No Friends</Card.Header>
          ) : (
            <>
              <Card.Header as="h2">Followers</Card.Header>
              {followers?.map((follower: User) => (
                <UserCard user={follower} key={follower.id} />
              ))}
            </>
          )}
        </Card.Body>
      </Card>
    </>
  );
};

export default Followers;

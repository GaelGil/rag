import Card from "react-bootstrap/Card";
import { Link } from "react-router-dom";
import type { UserProps } from "../../types/User";
import { Image } from "react-bootstrap";
import { getDefaultPhoto } from "../../api/helper";

const UserCard: React.FC<UserProps> = ({ user }) => {
  return (
    <>
      <Card>
        <Card.Body>
          <Card.Title>
            <Image
              src={user.pfp || getDefaultPhoto()}
              roundedCircle
              fluid
              alt="Profile Avatar"
              className="mb-2"
              style={{
                width: "100px",
                height: "100px",
                objectFit: "cover",
              }}
            />
            <Link to={`/user/${user.id}`}>{user.username}</Link>
          </Card.Title>
        </Card.Body>
      </Card>
    </>
  );
};

export default UserCard;

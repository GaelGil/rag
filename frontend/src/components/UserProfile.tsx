import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Card, Container, Row, Col, Spinner, Image } from "react-bootstrap";
import { useUser } from "../context/UserContext";
import { getDefaultPhoto } from "../api/helper";

const UserProfile = ({ userId }: { userId?: string }) => {
  const { user, setUser } = useUser();
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchProfile = async () => {
      setLoading(true);
      try {
        console.log(user);
      } catch (error) {
        console.error("Error fetching profile:", error);
        navigate("/login");
      } finally {
        setLoading(false);
      }
    };

    fetchProfile();
  }, [userId, user, setUser, navigate]);

  return (
    <Container className="py-5">
      <Row className="justify-content-center">
        <Col xs={12} md={8}>
          <Card className="border-0 shadow-sm">
            <Card.Body>
              {loading ? (
                <div className="text-center py-4">
                  <Spinner animation="border" variant="primary" />
                  <Card.Title className="mt-3">Loading Profile...</Card.Title>
                </div>
              ) : user ? (
                <Row className="align-items-center">
                  <Col xs={4} className="text-center">
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
                  </Col>
                  <Col xs={8}>
                    <h4 className="mb-1">@{user.username}</h4>
                    <div className="d-flex gap-3 mt-2">
                      <Card.Subtitle
                        onClick={() => navigate(`/edit-profile/${user.id}`)}
                        style={{
                          cursor: "pointer",
                          color: "blue",
                          textDecoration: "underline",
                        }}
                      >
                        Edit Profile
                      </Card.Subtitle>
                    </div>
                  </Col>
                </Row>
              ) : (
                <div className="text-center py-4">
                  <Card.Title>No profile data found</Card.Title>
                </div>
              )}
            </Card.Body>
          </Card>
        </Col>
      </Row>
    </Container>
  );
};

export default UserProfile;

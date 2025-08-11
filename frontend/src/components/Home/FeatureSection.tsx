import { Container, Row, Col, Card } from "react-bootstrap";

const FeaturesSection = () => {
  const features = [
    {
      title: "Connect with Friends",
      description: "Find and connect with people who share your interests.",
    },
    {
      title: "Chat and Share",
      description: "Send messages, share posts, and stay updated.",
    },
    {
      title: "React to Posts",
      description: "Like and comment on content shared by your network.",
    },
  ];

  return (
    <Container className="my-5">
      <h2 className="text-center mb-4">Features</h2>
      <Row>
        {features.map((feature, index) => (
          <Col md={4} key={index} className="mb-4">
            <Card className="text-center h-100">
              <Card.Body>
                {/* <div className="mb-3">{feature.icon}</div> */}
                <Card.Title>{feature.title}</Card.Title>
                <Card.Text>{feature.description}</Card.Text>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default FeaturesSection;

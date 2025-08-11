import { Container, Row, Col, Card } from "react-bootstrap";

const Testimonials = () => {
  const testimonials = [
    {
      name: "Alice",
      feedback: "Lorem, ipsum dolor sit amet consectetur adipisicing elit ",
    },
    {
      name: "Bob",
      feedback: "Lorem, ipsum dolor sit amet consectetur adipisicing elit ",
    },
    {
      name: "Charlie",
      feedback: "Lorem, ipsum dolor sit amet consectetur adipisicing elit ",
    },
  ];

  return (
    <Container className="my-5">
      <h2 className="text-center mb-4">What People Are Saying</h2>
      <Row>
        {testimonials.map((t, i) => (
          <Col md={4} key={i}>
            <Card className="mb-4">
              <Card.Body>
                <Card.Text>"{t.feedback}"</Card.Text>
                <Card.Subtitle className="text-muted text-end">
                  — {t.name}
                </Card.Subtitle>
              </Card.Body>
            </Card>
          </Col>
        ))}
      </Row>
    </Container>
  );
};

export default Testimonials;

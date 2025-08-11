import { Container, Row, Col } from "react-bootstrap";

const AboutSection = () => {
  return (
    <Container className="my-5">
      <Row>
        <Col md={6}>
          <h2>About Us</h2>
          <p>
            Lorem ipsum dolor sit amet consectetur, adipisicing elit.
            Perferendis quibusdam ipsa, dolorum maiores tenetur in impedit cum
            culpa ad voluptatum est reiciendis officiis odio, doloribus adipisci
            rerum quas incidunt harum!
          </p>
        </Col>
        <Col md={6}>
          <img
            src="https://via.placeholder.com/500x300"
            alt="About"
            className="img-fluid"
          />
        </Col>
      </Row>
    </Container>
  );
};

export default AboutSection;

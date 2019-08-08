context('login_view', () => {
    before(() => {
       cy.fixture("credentials").as("credentials");
    });

    beforeEach(() => {
        cy.visit("/login");
    });

    it ("should allow logging in with correct credentials", () => {
        cy.get("@credentials").then((credentials) => {
            cy.get("#email").type(credentials.email)
            cy.get("#password").type(credentials.password);
            cy.get("#remember").click();
            cy.get("#submit").click();
            cy.url().should("eq", Cypress.config().baseUrl + "/");
        });
    });
});



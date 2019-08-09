const login = () => {
    cy.fixture("credentials").then((credentials) => {
        cy.get("#email").type(credentials.email)
        cy.get("#password").type(credentials.password);
        cy.get("#remember").click();
        cy.get("#submit").click();
        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
}

context('login_view', () => {
    beforeEach(() => {
        cy.visit("/login");
    });

    it ("should allow logging in with correct credentials", login);

    it ("should allow logging out after logging in", () => {
        login();
        cy.get("#current-user-dropdown").click();
        cy.get("#log-out").click();
        cy.url().should("eq", Cypress.config().baseUrl + "/");
    });
});

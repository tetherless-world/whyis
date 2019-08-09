context('home_view', () => {
    beforeEach(() => {
        cy.visit("/");
    });

    it ("should allow anonymous access", () => {
    });

    it ("should have a link to login", () => {
        cy.get("a[href='/login'").click();
        cy.url().should("eq", Cypress.config().baseUrl + "/login");
    });

    // it ("should allow searching in the top search bar", () => {
    //     cy.get("input[type='search']").type("database");
    //     cy.contains("database").click()
    //     cy.url().should("eq", Cypress.config().baseUrl + "/about?uri=http%3A%2F%2Fsemanticscience.org%2Fresource%2FDatabase");
    // });
    // The bottom search bar uses the same HTML, and can't be distinguished.
});



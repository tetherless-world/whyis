Cypress.Commands.add('login', () => {
    // Just POSTing to the login form endpoint doesn't work, because of CSRF
    // cy.request({
    //     url: '/login',
    //     method: 'POST',
    //     body: {
    //         email: "whyis@whyis.com",
    //         password: "password",
    //         remember: "y"
    //     }
    // });

    cy.visit("/login")
        .get("#email").type("whyis@whyis.com")
        .get("#password").type("whyis")
    //.get("#remember").click()
        .get("#submit").click();

    cy.url().should("eq", Cypress.config().baseUrl + "/about?uri=http://purl.org/twc/dsa/policy/");
});

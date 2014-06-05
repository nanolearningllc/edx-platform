describe("JSInput", function() {
    beforeEach(function () {
        loadFixtures('js/capa/fixtures/jsinput.html');
        this.sections = $(document).find('section[id^="inputtype_"]');
        this.inputFields = $(document).find('input[id^="input_"]');
        JSInput.walkDOM();
    });

    it('sets all data-processed attributes to true on first load', function() {
        this.sections.each(function(index, item) {
            expect(item.attr('data-processed')).toEqual('true');
        });
    });

    it('sets the data-processed attribute to true on subsequent load', function() {
        var section1 = $(this.sections[0]);
        var section2 = $(this.sections[1]);
        section1.attr('data-processed', false);
        JSInput.walkDOM();
        expect(section1.attr('data-processed')).toEqual('true');
        expect(section2.attr('data-processed')).toEqual('true');
    });

    it('sets the waitfor attribute to its update function', function() {
        this.inputFields.each(function(index, item) {
            expect(item.data('waitfor')).toBeDefined();
        });
    });

    it('tests the correct number of sections', function () {
        expect(this.sections.length).toEqual(this.inputFields.length);
        expect(this.sections.length).toBeGreaterThan(0);
    });
});


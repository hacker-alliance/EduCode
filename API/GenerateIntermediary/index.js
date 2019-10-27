let shapeCompare = function(firstE1, firstE2) {
    let y1 = firstE1.boundingRectangle.topY;
    let y2 = firstE2.boundingRectangle.topY;

    if (y1 > y2) {
        return 1;
    }
    else if (y1 > y2) {
        return - 1;
    }
    else {
        return 0;
    }
}

Array.prototype.contains = function(element){
    return this.indexOf(element) > -1;
};

let shapeFilter = function(element) {
    let allowedCategories = ["inkDrawing", "inkWord"];
    if (element.category == "inkDrawing") {
        let allowedShapes  = ["ellipse",  "square", "rectangle", "triangle", "pengtagon"];
        if (allowedShapes.contains(element.recognizedObject)) {
            return true;
        }
        else {
            return false;
        }
    }
    else if (element.category == "inkWord") {
        return true;
    }
    else {
        return false;
    }
}


module.exports = async function (context, req) {
    context.log('JavaScript HTTP trigger function processed a request.');

    //if (req.query.name || (req.body && req.body.name)) {
    if (true) {
        // Get Recognition Unit Array
        let shapes = req.body.recognitionUnits;

        //Filter Out Invalid Shapes
        shapes.filter(shapeFilter);

        // Sort Recognition Units
        shapes.sort(shapeCompare);


        let response = {
            shapes
        }

        context.res = {
            // status: 200, /* Defaults to 200 */
            // body: "Hello " + (req.query.name || req.body.name)
            body: response
        };
    }
    else {
        context.res = {
            status: 400,
            body: "Please pass a name on the query string or in the request body"
        };
    }
};
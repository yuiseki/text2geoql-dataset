[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
(
  nwr["tourism"="viewpoint"](area.outer);
);
out geom;

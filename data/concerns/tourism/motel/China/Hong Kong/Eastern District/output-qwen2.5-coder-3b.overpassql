[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
(
  nwr["tourism"="motel"](area.outer);
);
out geom;

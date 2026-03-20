[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
(
  nwr["shop"="florist"](area.outer);
);
out geom;

[out:json][timeout:30];
area["name:en"="Hong Kong"][boundary=administrative]->.outer;
(
  nwr["shop"~"supermarket"](area.outer);
);
out geom;

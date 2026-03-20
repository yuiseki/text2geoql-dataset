[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["shop"~"supermarket"](area.outer);
);
out geom;

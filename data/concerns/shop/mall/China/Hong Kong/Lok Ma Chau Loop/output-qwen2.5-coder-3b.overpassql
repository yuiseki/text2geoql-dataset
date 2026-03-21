[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["shop"~"mall"](area.outer);
);
out geom;

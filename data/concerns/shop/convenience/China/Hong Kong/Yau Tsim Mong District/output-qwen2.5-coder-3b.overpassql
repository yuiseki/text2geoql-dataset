[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["shop"="convenience"](area.outer);
);
out geom;

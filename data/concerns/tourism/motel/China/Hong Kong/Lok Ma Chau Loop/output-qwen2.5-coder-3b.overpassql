[out:json][timeout:30];
area["name:en"="Hong Kong"]->.outer;
(
  nwr["tourism"="motel"](area.outer);
);
out geom;

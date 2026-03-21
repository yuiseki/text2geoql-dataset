[out:json][timeout:30];
area["name:en"="Shenzhen"]->.outer;
(
  nwr["cuisine"~"mexican"](area.outer);
);
out geom;

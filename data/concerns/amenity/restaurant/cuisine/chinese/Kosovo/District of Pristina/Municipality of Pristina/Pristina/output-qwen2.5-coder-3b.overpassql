[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
(
  nwr["cuisine"~"chinese"](area.outer);
);
out geom;

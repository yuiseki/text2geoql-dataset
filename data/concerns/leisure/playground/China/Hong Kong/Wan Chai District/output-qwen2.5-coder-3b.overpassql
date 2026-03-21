[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["leisure"~"playground"](area.outer);
);
out geom;

[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["leisure"~"garden"](area.outer);
);
out geom;

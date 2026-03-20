[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["railway"~"station"](area.outer);
);
out geom;

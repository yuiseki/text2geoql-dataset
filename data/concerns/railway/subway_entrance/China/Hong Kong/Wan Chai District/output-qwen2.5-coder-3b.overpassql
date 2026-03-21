[out:json][timeout:30];
area["name:en"="Wan Chai District"]->.outer;
(
  nwr["railway"~"subway"](area.outer);
);
out geom;

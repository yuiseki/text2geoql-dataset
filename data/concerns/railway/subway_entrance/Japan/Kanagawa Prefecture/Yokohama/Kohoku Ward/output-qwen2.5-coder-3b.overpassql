[out:json][timeout:30];
area["name:en"="Kohoku Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["railway"~"subway"](area.inner)(area.outer);
);
out geom;

[out:json][timeout:30];
area["name:en"="Totsuka Ward"]->.outer;
area["name:en"="Yokohama"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;

[out:json][timeout:30];
area["name:en"="Pristina"]->.outer;
area["name:en"="Municipality of Pristina"]->.inner;
(
  nwr["shop"~"optician"](area.inner)(area.outer);
);
out geom;

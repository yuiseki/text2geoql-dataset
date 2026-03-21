[out:json][timeout:30];
area["name:en"="Hakata Ward"]->.outer;
area["name:ja"="福岡市"]->.inner;
(
  nwr["historic"~"tomb"](area.inner)(area.outer);
);
out geom;

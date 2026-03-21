[out:json][timeout:30];
area["name:ja"="長崎県"]->.outer;
area["name:ja"="長崎市"]->.inner;
(
  nwr["historic"~"ruins"](area.inner)(area.outer);
);
out geom;

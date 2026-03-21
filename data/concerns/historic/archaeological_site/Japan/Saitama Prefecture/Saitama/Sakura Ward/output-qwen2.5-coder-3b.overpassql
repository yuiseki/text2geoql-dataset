[out:json][timeout:30];
area["name:ja"="桜区"]->.outer;
area["name:ja"="埼玉県"]->.inner;
(
  nwr["historic"~"archaeological"](area.inner)(area.outer);
);
out geom;

[out:json][timeout:30];
area["name:en"="Fukuoka"]->.outer;
area["name:ja"="福岡県"]->.inner;
(
  nwr["craft"~"pottery"](area.inner)(area.outer);
);
out geom;

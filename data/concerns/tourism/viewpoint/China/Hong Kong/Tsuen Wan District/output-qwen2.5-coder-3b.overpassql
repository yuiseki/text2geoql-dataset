[out:json][timeout:30];
area["name:en"="Tsuen Wan District"][boundary=administrative]->.outer;
area["name:en"="Tsuen Wan District"]->.inner;
(
  nwr["tourism"="viewpoint"](area.inner)(area.outer);
);
out geom;

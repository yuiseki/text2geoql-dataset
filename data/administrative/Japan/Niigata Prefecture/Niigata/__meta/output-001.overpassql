// Important note: SubArea: Japan/Niigata Prefecture/Niigata
[out:json][timeout:30000];
area["name:en"="Niigata Prefecture"]->.outer;
area["name:en"="Niigata"]->.inner;
(
  relation["boundary"="administrative"]["admin_level"=8](area.inner)(area.outer);
);
out meta;
